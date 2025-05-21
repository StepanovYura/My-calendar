<template>
  <div class="notification"></div>
  <main class="container">
    <div class="views">
      <div class="choice-friend">
        <input type="checkbox" id="filter-message-requestToFriend" name="filter-message" value="request">
        <label for="filter-message-requestToFriend">Запросы в друзья</label>

        <input type="checkbox" id="filter-message-alert" name="filter-message" value="alert">
        <label for="filter-message-alert">Оповещения</label>
      </div>
      <div class="calendary">
        <p>Заглушка</p>
      </div>
    </div>
  </main>
  <footer>
    <p>Пока заглушка</p>
  </footer>
</template>


<style scoped>
body {
    font-family: "Arial", sans-serif;
    display: flex;
    flex-direction: column;
    min-height: 100vh;

    background-color: white;
    color: #333;
}

.navbar {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    padding: 0 2rem 0 2rem;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search {
    visibility: hidden;
}

.nav-buttons {
    display: flex;
    gap: 1rem;
    margin-left: 80px;
}

.nav-buttons img {
    max-block-size: 30px;
    transition: all 0.3s ease; /* Плавное изменение размера */
}

#add-event-button > img:hover,
.icons > img:hover,
.icons.active > img {
    transform: scale(1.2);
    border-radius: 50%;
}

#add-event-button > img {
    transition: all 0.3s ease; /* Плавное изменение размера */
}

.theme {
    background: none;
    border: none;
    cursor: pointer;
}

.notification {

}

.container {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
    flex-grow: 1;
}

.holder-choice {
    flex: 1;
    display: flex;
    flex-direction: row;
    max-height: 70px;

    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
}

#choice {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 1rem 0 1rem;
}

.choice-friend {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: start;

    padding: 2rem 1rem 0 1rem;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
    gap: 5px;

}

.match-btn {
  color: #333;
  background-color: rgb(209, 204, 204);
  min-height: 40px;
  min-width: 120px;
}

#range-select {
    margin-top: 5px;
}

.views {
    flex: 8;
    display: flex;
    flex-direction: row;
    gap: 1rem;

    background-color: white;
    border-radius: 4px;
}

.view-choice {
    flex: 8;
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: 1rem;

    background-color: white;
    border-radius: 4px;
}

.calendary {
    flex: 8;

    background-color: white;
    border-radius: 4px;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
}

#add-event-button {
    position: absolute;
    right: 50px;
    top: 700px;
    background: none;
    border: none;
    padding: 0;
    margin: 0;
    cursor: pointer;
    outline: none;
}

footer {
    min-height: 90px;
    padding-left: 20px;
}


</style>