def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_score = None

    resource_set = set(resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        ns = (nx, ny)

        # Evaluate this step by how much it helps us reach good resources while denying opponent.
        step_best = None
        for r in resources:
            if r == ns:
                candidate = (10**9, 0)  # immediate collection
            else:
                self_d = manh(ns, r)
                opp_d = manh((ox, oy), r)

                # Prefer resources where opponent is farther; break ties toward smaller self distance.
                # Also bias toward moves that do not worsen our distance too much.
                candidate = ((opp_d - self_d), (-self_d))
            if step_best is None or candidate > step_best:
                step_best = candidate

        if step_best is None:
            continue

        # If we didn't move but opponent is closer to the best resource, prefer moving.
        # Deterministic mild tie-break: prefer increasing closeness to currently best resource.
        cur_best = max(resources, key=lambda r: (manh((ox, oy), r) - manh((sx, sy), r), -manh((sx, sy), r)))
        if step_best[0] == (manh((ox, oy), cur_best) - manh(ns, cur_best)):
            tiebreak = -manh(ns, cur_best)
        else:
            tiebreak = step_best[1]

        final_score = (step_best[0], tiebreak, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or final_score > best_score:
            best_score = final_score
            best_move = [dx, dy]

    # If all invalid, stay.
    return best_move if best_move is not None else [0, 0]