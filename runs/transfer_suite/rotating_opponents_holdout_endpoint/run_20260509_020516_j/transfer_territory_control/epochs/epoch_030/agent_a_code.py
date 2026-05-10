def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    self_set = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))
    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if unclaimed:
        cx = sum(x for x, y in unclaimed) // len(unclaimed)
        cy = sum(y for x, y in unclaimed) // len(unclaimed)
        dist_to_unclaimed = min(man(sx, sy, x, y) for x, y in unclaimed)
        target_mode = 1 if dist_to_unclaimed <= 3 else 0
    else:
        cx, cy, target_mode = ox, oy, 0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        is_self = cell in self_set
        is_opp = cell in opp_set
        is_uncl = (cell not in self_set and cell not in opp_set)

        # Attraction toward unclaimed centroid; slight bias toward closest edges of opponent.
        base_tx, base_ty = (cx, cy) if target_mode == 1 else (ox, oy)
        goal_dist = man(nx, ny, base_tx, base_ty)
        opp_prox = min((man(nx, ny, x, y) for (x, y) in opp_set), default=man(nx, ny, ox, oy))

        # Territory-flip incentive: entering opponent-owned should be strongly preferred.
        flip_bonus = 25 if is_opp else 0
        self_penalty = -2 if is_self else 0
        unclaimed_bonus = 6 if is_uncl else 0

        # Avoid immediate "stalling" when unclaimed exists.
        move_progress = -goal_dist
        if unclaimed:
            move_progress += 0.5 * (3 - man(nx, ny, base_tx, base_ty) if man(nx, ny, base_tx, base_ty) <= 3 else -2)

        val = flip_bonus + unclaimed_bonus + self_penalty + move_progress - 0.35 * opp_prox
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]