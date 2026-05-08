def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    nbrs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Build a small deterministic target set: unclaimed cells adjacent to our territory.
    targets = set()
    if self_terr:
        for (x, y) in self_terr:
            for dx, dy in nbrs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    targets.add((nx, ny))

    cx, cy = w // 2, h // 2
    if not targets:
        # Fallback: choose unclaimed closest to our position, else center.
        if unclaimed:
            targets = {min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))}
        else:
            targets = {(cx, cy)}

    def score_cell(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        dself = abs(nx - sx) + abs(ny - sy)
        dcenter = abs(nx - cx) + abs(ny - cy)
        # Prefer expanding to unclaimed; also punish giving up frontier.
        if (nx, ny) in opp_terr:
            base = 7
        elif (nx, ny) in unclaimed:
            base = 10
        elif (nx, ny) in self_terr:
            base = 2
        else:
            base = 1
        # Encourage staying near targets and away from opponent.
        best_target_dist = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets)
        dopp = abs(nx - ox) + abs(ny - oy)
        return base * 100 - dself * 3 - best_target_dist * 20 - dcenter * 0.1 + dself * 0.0 + dself * 0.0 + (dopp * 0.05)

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: fixed move order already in nbrs.
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]