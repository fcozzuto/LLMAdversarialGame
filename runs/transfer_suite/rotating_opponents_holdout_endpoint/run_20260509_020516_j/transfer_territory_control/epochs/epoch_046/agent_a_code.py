def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed_cells = observation.get("unclaimed_cells") or []
    unclaimed = set()
    for c in unclaimed_cells:
        if c and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    opp_terr_list = observation.get("opponent_territory") or []
    opp_terr = set()
    for t in opp_terr_list:
        if t and len(t) >= 2:
            opp_terr.add((int(t[0]), int(t[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    targets = list(unclaimed)[:32]  # deterministic cap
    if not targets:
        targets = [(ox, oy)]
    # If opponent territory is present, also consider nearby stealing
    opp_targets = list(opp_terr)[:24]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Prefer claiming nearby unclaimed; also slightly prefer moving toward opponent when it helps steal.
        mind_unclaimed = 10**9
        for t in targets:
            if inb(t[0], t[1]):
                d = dist((nx, ny), t)
                if d < mind_unclaimed:
                    mind_unclaimed = d
        d_opp = dist((nx, ny), (ox, oy))

        # Steal incentive: entering opponent territory is huge; nearing it is moderate.
        steal = 0
        if (nx, ny) in opp_terr:
            steal += 5000
        else:
            # proximity to opponent territory
            md = 10**9
            for t in opp_targets:
                if inb(t[0], t[1]):
                    d = dist((nx, ny), t)
                    if d < md:
                        md = d
            if md < 6:
                steal += (6 - md) * 120

        # Obstacle-aware mild penalty: avoid corners with many blocked neighbors
        neigh_block = 0
        for ex, ey in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
            tx, ty = nx + ex, ny + ey
            if not inb(tx, ty) or (tx, ty) in obs:
                neigh_block += 1

        val = 1000 - mind_unclaimed * 22 - d_opp * 3 + steal - neigh_block * 2

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]