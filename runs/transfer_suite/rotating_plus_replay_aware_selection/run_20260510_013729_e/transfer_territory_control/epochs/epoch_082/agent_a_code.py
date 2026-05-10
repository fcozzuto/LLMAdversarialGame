def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    x, y = observation.get("self_position") or [0, 0]
    x, y = int(x), int(y)

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    opp_t = observation.get("opponent_territory") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            un.append((int(p[0]), int(p[1])))

    opp_set = set()
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    # Deterministic target choice: nearest unclaimed; else nearest opponent territory; else nearest to center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if un:
        tx, ty = min(un, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    elif opp_set:
        ots = list(opp_set)
        tx, ty = min(ots, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    else:
        tx, ty = int(round(cx)), int(round(cy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]
    s_center = -1.0  # maximize

    # Heuristic score for neighbor: move toward target; prefer capturing (unclaimed or opponent) over neutral
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # bonus if landing on opponent-owned (flip on entry enabled) or unclaimed
        land_bonus = 0.0
        if (nx, ny) in opp_set:
            land_bonus += 2.5
        else:
            # unclaimed list may be large; use observation-provided set check by linear scan only if needed rarely
            # keep deterministic and cheap: check membership by comparing to unclaimed only when un is non-empty
            if un:
                for ux, uy in un:
                    if ux == nx and uy == ny:
                        land_bonus += 2.0
                        break
        # slight preference for center to match territory_center_claim archetype
        dist_center = abs(nx - cx) + abs(ny - cy)
        center_score = -0.03 * dist_center
        score = -d + land_bonus + center_score
        if best is None or score > best or (score == best and (dx, dy) < tuple(best_move)):
            best = score
            best_move = [dx, dy]
    if best is None:
        return [0, 0]
    return best_move