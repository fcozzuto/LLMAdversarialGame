def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    their_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick targets: unclaimed adjacent to opponent territory; else nearest unclaimed; else move toward opponent.
    adj = set()
    for tx, ty in their_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    adj.add((nx, ny))
    if adj:
        candidates = sorted(adj, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        uc = list(unclaimed)
        if uc:
            candidates = sorted(uc, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        else:
            candidates = [(ox, oy)]

    tx, ty = candidates[0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0, -10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Score: move toward target, prefer taking unclaimed, lightly prefer entering opponent territory to flip.
        dist_before = abs(sx - tx) + abs(sy - ty)
        dist_after = abs(nx - tx) + abs(ny - ty)
        closer = dist_before - dist_after

        score = closer * 10
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in their_terr:
            score += 20
        if (nx, ny) in my_terr:
            score -= 5

        # Extra: avoid being stuck by preferring moves that are not "dead" (no unclaimed/territory nearby).
        neigh = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and ((ax, ay) in unclaimed or (ax, ay) in their_terr):
                    neigh = 1
        if neigh == 0:
            score -= 8

        if score > best[2]:
            best = (dx, dy, score)

    return [best[0], best[1]]