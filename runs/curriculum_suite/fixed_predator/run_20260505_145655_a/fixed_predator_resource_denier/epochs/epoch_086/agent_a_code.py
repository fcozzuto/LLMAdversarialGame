def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Candidate moves (stay allowed)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Evaluate by attacking our reach while denying opponent: prefer resources where opponent is closer,
    # and also increase the distance gap after our move.
    best = None
    for dx, dy, nx, ny in candidates:
        best_for_self = None
        best_for_opp = None
        # For each resource, compute reach and "denial" potential
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Deny targets where opponent is already closer or near-equal
            deny = 0
            if od - sd > 0:
                deny = (od - sd)
            # Also slightly favor shorter self distance
            val = -sd + 0.35 * deny - 0.002 * (rx + ry)
            if best_for_self is None or val > best_for_self:
                best_for_self = val

            # What would be opponent's best capture next turn (approx: static opponent)
            od2 = man(ox, oy, rx, ry)
            sd2 = man(nx, ny, rx, ry)
            # Gap if we move here: bigger means we are "safer" against opponent taking that resource
            gap = od2 - sd2
            val_opp = -od2 + 0.15 * gap
            if best_for_opp is None or val_opp > best_for_opp:
                best_for_opp = val_opp

        # Final score: maximize (our progress) and minimize opponent advantage
        # best_for_opp is higher when opponent is "able"; subtract it.
        score = (best_for_self if best_for_self is not None else -10**9) - 0.8 * (best_for_opp if best_for_opp is not None else 0)

        # Tie-break deterministically: prefer move that reduces our Manhattan distance to the currently best resource for us
        if best is None:
            best = (score, dx, dy)
        else:
            if score > best[0]:
                best = (score, dx, dy)
            elif score == best[0]:
                # smaller distance to nearest resource after move
                # compute quickly: use current nx,ny
                dmin = min(man(nx, ny, rx, ry) for rx, ry in resources)
                bdmin = min(man(sx + best[1], sy + best[2], rx, ry) for rx, ry in resources)
                if dmin < bdmin:
                    best = (score, dx, dy)

    return [int(best[1]), int(best[2])]