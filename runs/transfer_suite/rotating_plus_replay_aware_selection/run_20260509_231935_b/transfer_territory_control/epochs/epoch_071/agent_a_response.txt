def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list if isinstance(p, (list, tuple)) and len(p) == 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0: ax = -ax
        ay -= by
        if ay < 0: ay = -ay
        return ax + ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        d_self = man(nx, ny, sx, sy)
        d_to_opp = man(nx, ny, ox, oy)
        d_to_self = man(nx, ny, sx, sy)
        close_adv = d_to_opp - d_to_self  # + means closer to us than to opponent

        if (nx, ny) in opp_terr:
            v = 1000 + 6 * close_adv - d_to_opp + 0.2 * edge
        elif (nx, ny) in self_terr:
            v = 20 + 1.5 * close_adv - 0.2 * d_self + 0.2 * edge
        elif (nx, ny) in unclaimed:
            v = 60 + 8 * close_adv - 0.5 * d_to_opp + 0.1 * edge
        else:
            v = 10 + 2 * close_adv - 0.2 * d_to_opp

        # Avoid getting boxed in near obstacles
        neigh_obs = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ddx, ny + ddy
            if not inside(tx, ty) or (tx, ty) in obstacles:
                neigh_obs += 1
        v -= 2.0 * neigh_obs

        # Deterministic tie-break: prefer lower dx, then lower dy, then larger v
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]