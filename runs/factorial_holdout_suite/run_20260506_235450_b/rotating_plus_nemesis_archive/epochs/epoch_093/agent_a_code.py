def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (-(10**18), 10**9, 10**9, 0, 0)  # (lead, -oppDist, -myDist, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_for_move = (-(10**18), -10**9, -(10**18))  # (lead, -oppDist, -myDist)
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            lead = opd - myd  # positive means we arrive no later than opponent (in distance steps)
            # Prefer resources we can get first; if all equal, prefer closer, then prefer farther opponent distance.
            cand = (lead, -opd, -myd)
            if cand > best_for_move:
                best_for_move = cand

        lead, nOpp, nMy = best_for_move
        # Final tie-break: deterministic order via dx,dy values.
        cand_all = (lead, nOpp, nMy, dx, dy)
        if cand_all > best:
            best = cand_all

    return [best[3], best[4]]