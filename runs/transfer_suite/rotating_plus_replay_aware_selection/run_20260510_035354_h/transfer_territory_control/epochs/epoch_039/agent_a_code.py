def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        try:
            x, y = o
            if inb(x, y): obs.add((x, y))
        except: 
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    un_list = observation.get("unclaimed_cells") or []
    un = []
    for p in un_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                un.append((x, y))
    if not un:
        un = [observation.get("opponent_position", (ax, ay))]

    opx, opy = observation.get("opponent_position", (ax, ay))
    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = ax, ay
            dx, dy = 0, 0
        d_un = min(cheb(nx, ny, x, y) for x, y in un[:25])
        d_op = cheb(nx, ny, opx, opy)
        v = -d_un * 3 - d_op
        if observation.get("scores") is not None:
            my = 0
            try: my = observation["scores"].get("self", 0) or observation["scores"].get(0, 0)
            except: my = 0
            v += my * 0
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]