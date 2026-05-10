def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = (10**9, 10**9, 10**9, 10**9, None)  # (score, dist_self, dist_op, -unclaimedAdj, target)
    if not unclaimed:
        targets = list(op_terr) if op_terr else list(self_terr)
        unclaimed = targets[:]

    target = None
    for tx, ty in unclaimed[:64]:
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        ds = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        # prioritize cells we can reach earlier and that are near our boundary
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if (nx, ny) in self_terr:
                    adj += 1
        score = (ds - do, ds, do, -adj)
        if score < best[:4]:
            best = (score[0], score[1], score[2], score[3], (tx, ty))
    target = best[4] if best[4] is not None else (sx, sy)

    tx, ty = target
    # choose best immediate move that moves toward target and avoids obstacles
    best_move = (10**9, 10**9, None)  # (d_to_target, penalty, move)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # slight boost for entering opponent territory (flipping is enabled)
        flip_boost = -1 if (nx, ny) in op_terr else 0
        penalty = d + (0 if (nx, ny) in self_terr else 0) + (-flip_boost)
        cand = (d, penalty, (dx, dy))
        if cand[0] < best_move[0] or (cand[0] == best_move[0] and cand[1] < best_move[1]):
            best_move = cand
    return list(best_move[2] if best_move[2] is not None else (0, 0))