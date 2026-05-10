def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    best_move = None
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [int(dx), int(dy)]
        d = cheb(nx, ny, ox, oy)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)

    if best_move is not None:
        return [int(best_move[0]), int(best_move[1])]
    return [0, 0]