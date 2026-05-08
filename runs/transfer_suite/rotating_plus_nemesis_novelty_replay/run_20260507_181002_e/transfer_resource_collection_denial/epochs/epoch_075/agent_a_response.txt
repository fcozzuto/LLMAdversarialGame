def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best immediate move by maximizing "own arrival advantage" among reachable targets.
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Evaluate this move against best contested resource.
        move_best = -(10**18)
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            # Favor cells we can reach earlier, strongly.
            advantage = opp_d - self_d
            score = 0
            if self_d == 0:
                score += 10**6
            score += 2000 * advantage
            # If we can't beat opponent, still move toward nearer resources but devalue.
            if advantage < 0:
                score += -400 * (-advantage)
            # Small tie-break: prefer getting closer than farthest.
            score += -self_d
            if score > move_best:
                move_best = score
        if move_best > best[0]:
            best = (move_best, dx, dy)
        # Deterministic tie-break: lexicographically smaller move.
        elif move_best == best[0]:
            if (dx, dy) < (best[1], best[2]):
                best = (move_best, dx, dy)

    return [int(best[1]), int(best[2])]