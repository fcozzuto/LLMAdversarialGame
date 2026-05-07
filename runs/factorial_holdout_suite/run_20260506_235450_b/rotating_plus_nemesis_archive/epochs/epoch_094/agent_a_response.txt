def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = [r for r in resources if r not in obstacles]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer moves that secure a resource where we are closer than opponent.
    # If no such resource, choose a move that improves the lead margin most.
    best = None  # (lead, -my_d, -opp_d, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cand = None
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            lead = opp_d - my_d  # positive => we are closer after move
            # Tie-break: prefer closer overall; also prefer not giving opponent immediate advantage.
            score = (lead, -my_d, -opp_d)
            if cand is None or score > cand:
                cand = score
        if cand is None:
            continue

        # Second-level tie-break: avoid stepping into "pressure": cells adjacent to obstacles that may trap us.
        # Deterministic small bias only.
        trap = 0
        for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)]:
            if (ax, ay) in obstacles:
                trap += 1
        score2 = (cand[0], cand[1], cand[2], -trap, dx, dy)
        if best is None or score2 > best:
            best = score2

    return [int(best[4]), int(best[5])]