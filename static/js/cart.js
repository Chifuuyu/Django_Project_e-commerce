const updateCart = document.getElementsByClassName('update-cart');
for (let i = 0; i < updateCart.length; i++) {
	updateCart[i].addEventListener('click', ()=> {
        const productId = updateCart[i].dataset.product
        const action = updateCart[i].dataset.action
        const value = 0
        console.log('productId:', productId, 'Action:', action)
        updateUserOrder(productId, action, value)
        }
    )
}
