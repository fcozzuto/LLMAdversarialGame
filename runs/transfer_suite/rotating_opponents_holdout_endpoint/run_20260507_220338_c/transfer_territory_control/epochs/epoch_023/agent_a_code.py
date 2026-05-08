def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    un_list = list(un)
    # Limit computation: only consider nearby unclaimed targets
    if un_list:
        un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - ox) + abs(p[1] - oy)))
        un_list = un_list[:20]
    else:
        un_list = []

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        is_un = (nx, ny) in un
        is_my = (nx, ny) in my
        is_opp = (nx, ny) in opp

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_my = abs(nx - sx) + abs(ny - sy)
        base = 0

        if is_opp:
            base += 260  # strong for flipping into opponent territory
            base += 20 * (1 if d_opp > 0 else 0)
        elif is_my:
            base += 10  # maintain control
        elif is_un:
            base += 140  # claim unclaimed
        else:
            base += 0

        # Prefer moving toward unclaimed frontier and away from immediate opponent threat
        if un_list:
            best_un = 10**9
            for tx, ty in un_list:
                # Encourage steps that reduce distance to some promising unclaimed cell
                d = abs(tx - nx) + abs(ty - ny)
                if d < best_un:
                    best_un = d
            base += 70 - 12 * best_un

        # Discourage walking into opponent's close reach (territory counterclaim)
        base += -28 * max(0, 6 - d_opp)

        # Small tie-breaker: keep moving (avoid idle unless best)
        base += 3 * (1 if (dx != 0 or dy != 0) else 0) - 2 * d_my

        # Deterministic tie-break: fixed direction ordering
        candidates.append((base, dirs.index((dx, dy)), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]