def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy(p):
        if p is None:
            return None
        try:
            if isinstance(p, dict):
                x, y = p.get("x"), p.get("y")
            else:
                x, y = p[0], p[1]
            x, y = int(x), int(y)
        except Exception:
            return None
        if 0 <= x < W and 0 <= y < H:
            return (x, y)
        return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = to_xy(p)
        if q is not None:
            obstacles.add(q)

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        q = to_xy(p)
        if q is not None:
            unclaimed.add(q)

    resources = set()
    for p in observation.get("resources") or []:
        q = to_xy(p)
        if q is not None:
            resources.add(q)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in unclaimed:
            val += 1000
        if (nx, ny) in resources:
            val += 200
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        val += d_to_opp  # prefer pushing away from opponent
        if resources:
            d_to_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            val -= d_to_res
        if unclaimed:
            d_to_uc = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed)
            val -= 0.5 * d_to_uc
        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val and best is not None:
            if [dx, dy] < best:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best