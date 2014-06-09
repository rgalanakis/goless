package main

import "fmt"
import "time"

const queueLen int = 10000
type timing float64

func benchChannel(chanSize int) timing {
	c := make(chan int, chanSize)
	go func() {
		for i := 0; i <= queueLen; i++ {
			c <- 0
		}
		close(c)
	}()

	start := time.Now()
	for i := 0; i < queueLen; i++ {
		<-c
	}
	elapsed := time.Since(start)
	return timing(elapsed.Seconds())
}

func benchChannels() {
	tookSync := benchChannel(0)
	writeResult("chan_sync", tookSync)
	tookAsync := benchChannel(queueLen + 1)
	writeResult("chan_async", tookAsync)
	tookBuff := benchChannel(1000)
	writeResult("chan_buff", tookBuff)
}

func writeResult(benchName string, elapsed timing) {
	fmt.Printf("go go %s %.5f\n", benchName, elapsed)
}

func main() {
	benchChannels()
}
