def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def nearest_res_dist(x, y):
        if not resources:
            return 10**9
        md = 10**9
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if inb(rx, ry) or (rx, ry) == (x, y):
                    d = man(x, y, rx, ry)
                    if d < md:
                        md = d
        return md

    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dres = nearest_res_dist(nx, ny)
            dop = man(nx, ny, ox, oy)
            # Encourage resource acquisition, keep distance from opponent.
            score = (-3.0 * dres) + (0.7 * dop)
            # Prefer moves that reduce resource distance if possible.
            cur_dres = nearest_res_dist(sx, sy)
            if dres < cur_dres:
                score += 1.0
            if dop > man(sx, sy, ox, oy):
                score += 0.5
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move