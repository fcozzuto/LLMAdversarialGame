def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    self_role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int):
                res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opp_d = dist2(nx, ny, ox, oy)
        if self_role == "evader":
            base = opp_d
        else:
            base = -opp_d
        if res:
            rmin = 10**18
            for rx, ry in res:
                if valid(rx, ry):
                    d = dist2(nx, ny, rx, ry)
                    if d < rmin:
                        rmin = d
            if rmin == 10**18:
                rmin = 0
            val = base * 1000 - rmin
        else:
            val = base
        if best_val is None or val > best_val or (val == best_val and (abs(dx) + abs(dy)) < (abs(best_move[0]) + abs(best_move[1]))):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]