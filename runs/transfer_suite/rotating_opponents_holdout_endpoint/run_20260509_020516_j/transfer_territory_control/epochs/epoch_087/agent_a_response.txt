def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (W - 1, H - 1))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    selfT = set(tuple(p) for p in observation.get("self_territory") or [])
    oppT = set(tuple(p) for p in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [])
    resources = [tuple(p) for p in observation.get("resources") or [] if p and len(p) >= 2]

    # Pick a deterministic target: try to take unclaimed closer than opponent (or adjacent to frontier)
    if resources:
        tx, ty = resources[0]
    else:
        best = None
        for x, y in (unclaimed or oppT):
            if not inside(x, y) and (x, y) != (sx, sy):
                continue
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            frontier_bonus = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in oppT:
                        frontier_bonus += 3
                    if (nx, ny) in selfT:
                        frontier_bonus += 1
            val = (do - ds) * 2 + frontier_bonus + (8 if (x, y) in unclaimed else 0)
            if best is None or val > best[0] or (val == best[0] and (ds, do) < best[1]):
                best = (val, (ds, do), (x, y))
        if best:
            tx, ty = best[2]
        else:
            # Fallback: go to center-ish
            tx, ty = (W // 2, H // 2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Evaluate next-step candidates by immediate land value + progress to target + avoid being "behind" opponent
    best_m = (0, 0)
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell = (nx, ny)
        v = 0
        if cell in oppT:
            v += 6  # flipping opponent territory on entry
        elif cell in unclaimed:
            v += 3
        elif cell in selfT:
            v += 1

        ds_next = abs(nx - tx) + abs(ny - ty)
        ds_cur = abs(sx - tx) + abs(sy - ty)
        v += (ds_cur - ds_next) * 2

        do = abs(nx - ox) + abs(ny - oy)
        if cell in unclaimed:
            v += do * -0.5  # prefer points not immediately nearest to opponent

        if best_v is None or v > best_v:
            best_v = v
            best_m = [dx, dy]
    return best_m