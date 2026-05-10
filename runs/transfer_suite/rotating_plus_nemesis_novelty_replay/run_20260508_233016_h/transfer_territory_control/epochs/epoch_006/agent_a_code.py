def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        d = a - b
        return d if d >= 0 else -d

    def dist_to(px, py, qx, qy):
        return md(px, qx) + md(py, qy)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            gain = 2
        elif (nx, ny) in unclaimed:
            gain = 1
        else:
            gain = 0

        # Safety: prefer not to end adjacent to obstacles (reduces being forced by collisions)
        adj_obs = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                adj_obs += 1

        # If equal gain, move toward improving capture potential: unclaimed > opponent territory > opponent position
        if unclaimed:
            tgt = min(unclaimed, key=lambda p: dist_to(nx, ny, p[0], p[1]))
            chase = dist_to(nx, ny, tgt[0], tgt[1])
        elif opp_terr:
            tgt = min(opp_terr, key=lambda p: dist_to(nx, ny, p[0], p[1]))
            chase = dist_to(nx, ny, tgt[0], tgt[1])
        else:
            chase = dist_to(nx, ny, opp_pos[0], opp_pos[1])

        # Deterministic tie-breakers
        key = (-(gain * 1000 - adj_obs), chase, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]