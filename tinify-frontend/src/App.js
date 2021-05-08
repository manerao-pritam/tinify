import './App.css'
import React, { useState } from "react"
import axios from 'axios'
import validator from 'validator'

function App() {

  const [display_url, setDisplayUrl] = useState('')
  const [url, setInputUrl] = useState('')

  const handleRequest = (action) => {

    if (!url || !validator.isURL(url)) {
      alert('Please enter a valid url!')
      return
    }

    const postData = { url }

    axios.post(`web-server-url/${action}`, postData)
      .then(res => {
        setDisplayUrl(res.data)
      })
      .catch(err => alert(`Please enter a ${action === 'expand' ? 'tinified' : 'valid'} url!`))
  }

  return (
    <div className="App" >
      <main>
        <h1>Tinify</h1>
        <input type="text" id="input" placeholder="Enter URL here" onChange={event => setInputUrl(event.target.value)} />
        <div class="buttons">
          <button id="shorten" onClick={() => handleRequest('shorten')} >Shorten</button>
          <button id="expand" onClick={() => handleRequest('expand')} >Expand</button>
        </div>
        <section id="section"><a href={display_url} target="_blank" rel="noreferrer">{display_url}</a></section>
      </main>
    </div>
  )
}

export default App