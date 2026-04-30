def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = set((x, y) for x, y in obstacles)
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]
        bx, by = best
        bd = max(abs(bx - sx), abs(by - sy))
        for x, y in resources[1:]:
            d = max(abs(x - sx), abs(y - sy))
            if d < bd or (d == bd and (x + y) < (bx + by)):
                best, bx, by, bd = (x, y), x, y, d
        return (bx, by)

    tx, ty = best_target()

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            return -10**9
        # Prefer reducing distance to target; lightly avoid moving toward opponent unless it also helps target.
        dt = max(abs(tx - nx), abs(ty - ny))
        do = max(abs(ox - nx), abs(oy - ny))
        cur_do = max(abs(ox - sx), abs(oy - sy))
        return (-dt * 1000) + (cur_do - do) * 10 + (-(abs(dx) + abs(dy)))

    best = (0, 0)
    best_s = -10**9
    for dx, dy in deltas:
        s = score_move(dx, dy)
        if s > best_s:
            best_s, best = s, (dx, dy)

    return [best[0], best[1]]