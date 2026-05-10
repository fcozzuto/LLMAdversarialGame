def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (0, 0)
    ox, oy = int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < W and 0 <= by < H:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < W and 0 <= ry < H and (rx, ry) not in blocked:
                resources.append((rx, ry))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((int(x), int(y)) for x, y in self_terr if x is not None and y is not None)
    opp_set = set((int(x), int(y)) for x, y in opp_terr if x is not None and y is not None)
    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = [(int(x), int(y)) for x, y in unclaimed if x is not None and y is not None]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(a, b):
        return 0 <= a < W and 0 <= b < H and (a, b) not in blocked

    best = (None, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Base value: prefer capturing/opposing cells, then unclaimed, then resource.
        val = 0
        if (nx, ny) in self_set:
            val += 1
        if (nx, ny) in opp_set:
            val -= 6  # flipping on entry
        if (nx, ny) in unclaimed:
            val -= 2

        # Avoid getting stuck: small penalty for moving away from nearest target.
        if resources:
            d = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
            val += d * 0.8
        else:
            val += (abs(nx - ox) + abs(ny - oy)) * 0.15

        # Frontier pressure: prefer stepping toward squares adjacent to opponent territory if possible.
        adj_opp = False
        for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
            if 0 <= ax < W and 0 <= ay < H and (ax, ay) in opp_set:
                adj_opp = True
                break
        if adj_opp:
            val -= 3.5

        # If resources exist, also slightly prefer moving onto cells closest to them.
        if resources:
            curd = min(abs(rx - sx) + abs(ry - sy) for rx, ry in resources)
            newd = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
            val += (newd - curd) * 0.6

        # Deterministic tie-break toward lexicographically smaller move.
        cand = (dx, dy)
        if best[0] is None or val < best[1] or (val == best[1] and cand < best[0]):
            best = (cand, val)

    dx, dy = best[0] if best[0] is not None else (0, 0)
    return [int(dx), int(dy)]