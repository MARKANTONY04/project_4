<!-- checkout/templates/checkout/success.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
  <h1>Thank you for your purchase 🎉</h1>

  {% if order %}
    <p>Your order <strong>#{{ order.id }}</strong> has been placed successfully.</p>

    <h3>Order Summary</h3>
    <ul>
      {% for item in order.lineitems.all %}
        <li>
          {{ item.quantity }} × {{ item.product_name }}
          ({{ item.unit_price }} each) — 
          <strong>{{ item.line_total }}</strong>
        </li>
      {% endfor %}
    </ul>

    <p><strong>Total Paid:</strong> 
       {{ order.lineitems.all|map:"line_total"|sum }}</p>

    <hr>
    <h4>Customer Info</h4>
    <p>
      {{ order.full_name }} <br>
      {{ order.email }} <br>
      {{ order.phone_number }} <br>
      {{ order.address_line1 }} {{ order.address_line2 }} <br>
      {{ order.city }}, {{ order.postcode }}, {{ order.country }}
    </p>
  {% else %}
    <p>No order found — please check your email confirmation.</p>
  {% endif %}

  <a href="{% url 'home' %}" class="btn btn-primary mt-3">Return to Home</a>
</div>
{% endblock %}
