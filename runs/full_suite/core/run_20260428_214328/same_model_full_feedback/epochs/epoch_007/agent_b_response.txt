def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def dist_king(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not res:
        # Move toward opponent corner-ish to reduce their options
        tx, ty = (w - 1 if ox < w - 1 else 0), (h - 1 if oy < h - 1 else 0)
    else:
        # Target resource where we are relatively closer; if none, choose one that opp is likely to take soon but we can contest.
        best = None
        for rx, ry in res:
            sd = dist_manh(sx, sy, rx, ry)
            od = dist_manh(ox, oy, rx, ry)
            # higher is better; encourage being closer than opponent and also closer overall
            score = (od - sd) * 3 - sd
            # if we can reach in 1 step advantage, spike it
            if sd <= 1 and od > sd:
                score += 50
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # step score: get closer to target, keep distance from opponent, and avoid moving to king-adjacent squares
        d_to_t = dist_manh(nx, ny, tx, ty)
        d_to_o = dist_king(nx, ny, ox, oy)
        # If we can pick resource immediately, make it dominant
        on_resource = 1 if (nx, ny) in set(res) else 0
        val = -d_to_t * 4 + d_to_o * 2 + on_resource * 100
        if d_to_o <= 1:
            val -= 8  # reduce immediate contention
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]