def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    respos = [tuple(r) for r in resources if isinstance(r, (list, tuple)) and len(r) == 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    opp_exists = ox is not None and oy is not None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if not respos:
            best_move = (dx, dy)
            best_score = 0
            continue

        # Maximize advantage: be closer to (any) resource while keeping opponent far.
        best_adv = -10**18
        for rx, ry in respos:
            d_us = abs(nx - rx) + abs(ny - ry)
            if opp_exists:
                d_opp = abs(ox - rx) + abs(oy - ry)
                # Our advantage increases when we approach resources and opponent is farther from them.
                adv = (d_opp - d_us) * 4 - d_us
            else:
                adv = -d_us
            if adv > best_adv:
                best_adv = adv

        # Prefer moves that immediately collect if on a resource.
        immediate = 1 if (nx, ny) in obstacles else 0
        if (nx, ny) in set(respos):
            best_adv += 1000000
        # Small tie-break: reduce distance to the single closest resource.
        # (Deterministic and cheap.)
        min_d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in respos)
        score = best_adv - min_d * 0.001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]