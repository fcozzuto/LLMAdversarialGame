def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obs_set = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    if not resources:
        return [0, 0]

    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        md = abs(rx - x) + abs(ry - y)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer resources where we are closer; if tied, closer overall; then deterministic by position.
        tkey = (md - od, md, rx, ry)
        if best_t is None or tkey < best_t[0]:
            best_t = (tkey, (rx, ry))

    if best_t is None:
        return [0, 0]

    tx, ty = best_t[1]
    my_d0 = abs(tx - x) + abs(ty - y)
    od0 = abs(tx - ox) + abs(ty - oy)

    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        my_d = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        # Move that reduces our distance most; then increases opponent distance to target; then deterministic.
        score = (my_d, od0 - od, dx, dy, nx, ny)
        if best is None or score < best[0]:
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]