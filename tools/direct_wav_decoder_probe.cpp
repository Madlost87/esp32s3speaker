#include "audio_decoder.h"
#include <vector>
#include <algorithm>
#include <cstdio>
#include <cstring>
using namespace micro_decoder;
struct Sink : DecoderListener {
 size_t total=0;
 void on_stream_info(const AudioStreamInfo&) override {}
 void on_state_change(DecoderState) override {}
 size_t on_audio_write(const uint8_t*, size_t n, uint32_t) override { n=std::min(n,size_t(222)); total+=n; return n; }
};
int main() {
 std::vector<uint8_t> wav(44+73216,0);
 auto u16=[&](int p,unsigned v){wav[p]=v;wav[p+1]=v>>8;};
 auto u32=[&](int p,unsigned v){u16(p,v);u16(p+2,v>>16);};
 memcpy(wav.data(),"RIFF",4);u32(4,wav.size()-8);memcpy(wav.data()+8,"WAVEfmt ",8);
 u32(16,16);u16(20,1);u16(22,1);u32(24,22050);u32(28,44100);u16(32,2);u16(34,16);
 memcpy(wav.data()+36,"data",4);u32(40,73216);
 for (size_t size : {size_t(1024),size_t(4096),size_t(16384)}) {
  RingBuffer rb; rb.create(wav.size()+100); rb.write(wav.data(),wav.size(),0);
  AudioDecoder decoder(size); decoder.set_source(&rb); decoder.start(AudioFileType::WAV); Sink sink;
  for (int i=0;i<10000;i++) {
   auto state=decoder.decode(true,&sink,50);
   if (state==AudioDecoderState::FINISHED) {printf("buffer=%zu decoded=%zu\n",size,sink.total); break;}
   if (state==AudioDecoderState::FAILED || i==9999) return 1;
  }
  if (sink.total!=73216) return 2;
 }
}
