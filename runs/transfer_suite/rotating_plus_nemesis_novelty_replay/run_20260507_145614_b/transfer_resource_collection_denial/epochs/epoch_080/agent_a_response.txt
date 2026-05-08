def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def on_resource(x, y):
        for rx, ry in resources:
            if rx == x and ry == y:
                return True
        return False

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if on_resource(sx, sy):
        return [0, 0]

    # Select best target: prioritize resources where we can arrive earlier; otherwise contest.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # earlier is better; also prefer nearer when tied. Add small incentive to contest when opp is closer.
        key = (od - sd, -sd, -(abs(rx - (w - 1 - ox)) + abs(ry - (h - 1 - oy))), rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    # Evaluate next moves locally (no full search): choose move that most improves distance/contestation.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        # estimate opponent distance to the same target if they keep moving toward it
        od_now = cheb(ox, oy, tx, ty)
        # opponent step toward target (deterministic greedy)
        step_x = 0 if ox == tx else (1 if tx > ox else -1)
        step_y = 0 if oy == ty else (1 if ty > oy else -1)
        nxo, nyo = ox + step_x, oy + step_y
        if 0 <= nxo < w and 0 <= nyo < h and (nxo, nyo) not in obstacles:
            od_next = cheb(nxo, nyo, tx, ty)
        else:
            od_next = od_now

        immediate = 5.0 if on_resource(nx, ny) else 0.0
        # Prefer moves that keep/extend lead, and reduce distance to finish earlier.
        val = (od_next - d_self, -d_self, immediate, -abs(nx - ox) - abs(ny - oy), turns_remaining)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move