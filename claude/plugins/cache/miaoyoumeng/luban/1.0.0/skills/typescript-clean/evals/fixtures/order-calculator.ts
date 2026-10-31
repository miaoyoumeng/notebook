interface OrderItem {
  price: number;
  qty: number;
}

interface Customer {
  active: boolean;
}

interface Coupon {
  valid: boolean;
}

interface Order {
  items: OrderItem[];
  customer: Customer;
  coupon?: Coupon;
}

const calculate = (order: Order) => {
  if (order) {
    if (order.items && order.items.length > 0) {
      if (order.customer) {
        if (order.customer.active) {
          let total = 0;
          for (let i = 0; i < order.items.length; i++) {
            const item = order.items[i];
            if (item.price > 0) {
              total += item.price * item.qty;
            } else {
              throw new Error('invalid price');
            }
          }
          if (order.coupon) {
            if (order.coupon.valid) {
              total = total * 0.9;
            }
          }
          return { total, status: total > 0 ? 'ok' : 'error' };
        } else {
          throw new Error('inactive customer');
        }
      } else {
        throw new Error('customer required');
      }
    } else {
      throw new Error('empty order');
    }
  }
  throw new Error('order required');
};

const preview = (order: Order) => {
  if (!order.items.length) throw new Error('empty order');
  let total = 0;
  order.items.forEach((item) => {
    if (item.price <= 0) throw new Error('invalid price');
    total += item.price * item.qty;
  });
  return total;
};

// 旧实现，保留备查
// const oldCalculate = (order: Order) => {
//   const total = order.items.reduce((sum, item) => sum + item.price * item.qty, 0);
//   return { total, status: 'ok' };
// };
