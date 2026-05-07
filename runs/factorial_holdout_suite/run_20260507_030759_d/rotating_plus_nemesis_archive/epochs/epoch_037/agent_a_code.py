def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in res:
        return [0, 0]

    def dist_manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        if res:
            my_d = 10**9
            opp_d = 10**9
            my_min_res = None
            for rx, ry in res:
                d1 = dist_manh(nx, ny, rx, ry)
                d2 = dist_manh(ox, oy, rx, ry)
                if d1 < my_d:
                    my_d = d1
                    my_min_res = (rx, ry)
                if d2 < opp_d:
                    opp_d = d2
            # Prefer moves that let us reach a resource earlier than opponent.
            # Small deterministic tie-break prefers staying closer to our nearest resource.
            score = (opp_d - my_d) * 1000 - my_d
            if my_min_res is not None:
                # If a resource is exactly reachable now, strongly prefer that.
                if my_d == 0:
                    score += 10**6
                # Mildly avoid stepping into positions that are adjacent to obstacles (can trap).
                for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)]:
                    if (ax, ay) in obst:
                        score -= 3
                        break
        else:
            # No visible resources: drift toward center to reduce distance to future spawns (if any).
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -dist_manh(nx, ny, cx, cy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: lexicographic on (dx,dy).
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]