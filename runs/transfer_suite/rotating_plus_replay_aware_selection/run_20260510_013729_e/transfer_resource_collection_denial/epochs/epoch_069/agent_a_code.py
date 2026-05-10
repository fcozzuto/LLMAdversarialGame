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

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_target(px, py):
        best_v = -10**18
        best_sd = 10**18
        best = None
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            v = od - sd  # >0 means we can get there first
            if v > best_v or (v == best_v and (sd < best_sd)):
                best_v = v
                best_sd = sd
                best = (rx, ry, sd, od)
        return best_v, best

    cur_v, _ = best_target(sx, sy)

    best_move = (0, 0)
    best_score = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        v, tgt = best_target(nx, ny)
        rx, ry, sd, od = tgt
        # primary: gain relative to opponent arrival; secondary: shorter self distance; tertiary: progress beyond current advantage
        score = v * 1000 - sd
        if v < 0 and cur_v >= 0:
            score -= 500  # discourage falling behind when already ahead
        # micro-tiebreaker: prefer moves that get closer to the opponent along that target
        score -= (man(nx, ny, rx, ry) - man(sx, sy, rx, ry)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]