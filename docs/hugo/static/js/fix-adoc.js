// replace the default admonitions block with one that looks like the antora output to apply similar styling via adoc.css
window.addEventListener('load', function () {
    const admonitions = document.getElementsByClassName('admonition-block')
    for (let i = admonitions.length - 1; i >= 0; i--) {
      const elm = admonitions[i]
      const type = elm.classList[1]
      const text = elm.getElementsByTagName('p')[0].innerHTML
      const parent = elm.parentNode
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = `<div class="admonitionblock ${type}">
      <table>
        <tbody>
          <tr>
            <td class="icon">
              <i class="fa icon-${type}" title="${type}"></i>
            </td>
            <td class="content">
              ${text}
            </td>
          </tr>
        </tbody>
      </table>
    </div>`
  
      const input = tempDiv.childNodes[0]
      parent.replaceChild(input, elm)
    }
  })