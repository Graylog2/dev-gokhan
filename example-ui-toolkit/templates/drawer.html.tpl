{# The detail panel. htmx puts this into #drawer. Clicking the backdrop or Close empties #drawer again. #}
<dialog open class="drawer"
        hx-get="/drawer/close" hx-target="#drawer" hx-swap="innerHTML swap:200ms"
        hx-trigger="click[target.tagName=='DIALOG']">
  <article>
    <header>
      <button aria-label="Close" rel="prev"
              hx-get="/drawer/close"
              hx-trigger="click, keyup[key=='Escape'] from:body"></button>
      <h3>{{ name }}</h3>
    </header>

    {% for title, items in sections %}
      <h4>{{ title }}</h4>
      <table>
        <tbody>
          {% for field, value in items %}
            <tr><th scope="row">{{ field | label }}</th><td>{{ value | show }}</td></tr>
          {% endfor %}
        </tbody>
      </table>
    {% endfor %}
  </article>
</dialog>
