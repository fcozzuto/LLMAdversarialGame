def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = c - a
        if dx < 0:
            dx = -dx
        dy = d - b
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_adv(px, py):
        best = None
        bestv = -10**30
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            v = od - sd  # positive means we can get there first
            if v > bestv or (v == bestv and sd < (best[0] if best else 10**9)):
                bestv = v
                best = (sd, rx, ry)
        return bestv, (best[1], best[2]) if best else (None, None)

    cur_adv, _ = best_adv(sx, sy)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        step_block = 1 if (nx, ny) in obst else 0
        adv, _ = best_adv(nx, ny)
        # Prefer moves that increase advantage; penalize stepping into obstacles; slight tie-break toward progress.
        val = (adv - cur_adv) * 10000 + adv * 100 + (-man(nx, ny, ox, oy)) - step_block * 100000
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]