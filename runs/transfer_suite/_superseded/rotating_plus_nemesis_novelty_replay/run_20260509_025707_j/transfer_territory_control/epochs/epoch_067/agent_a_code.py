def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in observation.get("obstacles") or []}
    my_set = {(p[0], p[1]) for p in observation.get("self_territory") or []}
    opp_set = {(p[0], p[1]) for p in observation.get("opponent_territory") or []}
    unclaimed = {(p[0], p[1]) for p in observation.get("unclaimed_cells") or []}

    cx, cy = w // 2, h // 2

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    # Prioritize contesting the center (territory_center_claim nemesis), and only then attack.
    # Small deterministic tie-break favors diagonal and forward-ish movement.
    un_list = list(unclaimed) if unclaimed else []
    nearest_un = None
    if un_list:
        nearest_un = min(un_list, key=lambda p: dist((sx, sy), p))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        enter_opp = (nx, ny) in opp_set
        enter_un = (nx, ny) in unclaimed
        d_center = dist((nx, ny), (cx, cy))
        d_self = dist((nx, ny), (sx, sy))
        d_opp_target = dist((nx, ny), (cx, cy))  # center-attack proxy
        score = 0
        score += 20 if enter_opp else 0
        score += 3 if enter_un else 0
        score += (30 - d_center)  # closer to center is good
        if nearest_un is not None:
            score += 1.5 * (dist((sx, sy), nearest_un) - dist((nx, ny), nearest_un))
        score += -0.05 * d_self

        # tie-break: prefer staying still less, then diagonals
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            # deterministic tie-break
            cur = (dx != 0 and dy != 0, -abs(dx) - abs(dy), -abs(dy), -abs(dx))
            old = (best[0] != 0 and best[1] != 0, -abs(best[0]) - abs(best[1]), -abs(best[1]), -abs(best[0]))
            if cur > old:
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]