/*
	Golang implementation of this project's benchmark.py file.
	It should be a pretty direct mirror.

	The only questionable decision is the use of reflect.SelectCase,
	rather than Go's select statement.
	goless' select function is based on reflect.SelectCase,
	so this is "idiotmatic goless" (ugh),
	but Go programs rarely use reflect.SelectCase and instead use its
	select function.

	Using the select statement would probably speed things up.
	I'm not sure what the right thing to do is,
	so I chose the easier thing.
*/

package main

import (
	"fmt"
	"reflect"
	"runtime"
	"time"
)

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

func benchSelect(useDefault bool) timing {
    c := make(chan int, 0)

	caseCnt := 4
	if useDefault {
		caseCnt = 5
	}
	cases := make([]reflect.SelectCase, caseCnt)
	cases[0] = reflect.SelectCase{Dir: reflect.SelectSend, Chan: reflect.ValueOf(c), Send: reflect.ValueOf(0)}
	cases[1] = reflect.SelectCase{Dir: reflect.SelectRecv, Chan: reflect.ValueOf(c)}
	cases[2] = cases[0]
	cases[3] = cases[1]
	if useDefault {
		cases[4] = reflect.SelectCase{Dir: reflect.SelectDefault}
	}

    go func() {
		for {
			c <- 0
			<- c
		}
	}()

	start := time.Now()
	for i := 0; i <= queueLen; i++ {
		reflect.Select(cases)
	}
	elapsed := time.Since(start)
	return timing(elapsed.Seconds())
}

func benchSelects() {
	tookNoDefault := benchSelect(false)
	writeResult("select", tookNoDefault)
	tookWithDefault := benchSelect(true)
	writeResult("select_default", tookWithDefault)
}

func writeResult(benchName string, elapsed timing) {
	fmt.Printf("go %s %s %.5f\n", runtime.Compiler, benchName, elapsed)
}

func main() {
	benchChannels()
	benchSelects()
}
