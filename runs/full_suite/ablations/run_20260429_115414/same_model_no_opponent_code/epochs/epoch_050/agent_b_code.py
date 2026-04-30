def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    center = ((w - 1) // 2, (h - 1) // 2)
    best_move = [0, 0]
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            pos = (nx, ny)

            if resources:
                md = 10**9
                for rr in resources:
                    d = dist(pos, rr)
                    if d < md:
                        md = d
                to_res = -md
            else:
                to_res = -dist(pos, center)

            d_opp = dist(pos, (ox, oy))
            val = to_res * 10 + d_opp

            if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                best_val = val
                best_move = [dx, dy]

    return best_move