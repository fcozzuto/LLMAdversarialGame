def choose_move(observation):
    ax, ay = observation["self_position"]
    bx, by = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for x, y in obstacles:
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    if unclaimed:
        targets = []
        for x, y in unclaimed:
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))
                if len(targets) >= 25:
                    break
    else:
        targets = []

    if not targets:
        for x, y in (op_t or []):
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))
        if not targets:
            targets = [(bx, by)]

    attack = (observation.get("turn_index", 0) % 4) >= 2
    base_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Try to bias away from "staying in place" early if there are targets.
    best = None
    for dx, dy in base_moves:
        nx, ny = ax + dx, ay + dy
        if not inside(nx, ny):
            continue

        # Nearest target distance (unclaimed preferred, otherwise opponent territory)
        md = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d

        # Extra shaping:
        # - If attacking, prefer reducing distance to opponent.
        # - Prefer moves that do not immediately give opponent a close counterclaim (roughly: keep distance from opponent while moving toward targets).
        opd = abs(bx - nx) + abs(by - ny)

        # - Prefer moving "toward" territory front: if our territory exists, prefer increasing distance from our current centroid? Actually prefer expanding outward:
        if my_t:
            cx = sum(x for x, y in my_t) / len(my_t)
            cy = sum(y for x, y in my_t) / len(my_t)
            expand = -((nx - cx) ** 2 + (ny - cy) ** 2)  # higher = less negative = closer; we want larger magnitude, so invert by subtracting squared distance
            expand = ((nx - cx) ** 2 + (ny - cy) ** 2)
        else:
            expand = 0

        # - Penalize staying still slightly unless late or no targets.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        late = 1 if observation.get("turn_index", 0) > 0.8 * max(1, observation.get("turn_index", 0) + 1) else 0

        score = (-md
                 + (0.25 * (0 if not attack else (w + h - opd)))  # attack: closer to opponent is better
                 - (0.08 * (0 if not attack else 0))  # keep deterministic simple
                 + 0.01 * expand
                 - 0.3 * stay_pen)

        # Tie-break deterministically by coordinates and move
        key = (score, -opd, ny, nx, dx, dy)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]