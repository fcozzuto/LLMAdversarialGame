def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        if res:
            best = None
            best_key = None
            for rx, ry in res:
                d_me = cheb(sx, sy, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                key = (d_opp - d_me, -d_me, (rx + 31 * ry) % 97)
                if best_key is None or key > best_key:
                    best_key = key
                    best = (rx, ry)
            return best
        return (ox, oy)

    tx, ty = pick_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        score = (d_opp - d_me, -d_me, -(dx * dx + dy * dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]