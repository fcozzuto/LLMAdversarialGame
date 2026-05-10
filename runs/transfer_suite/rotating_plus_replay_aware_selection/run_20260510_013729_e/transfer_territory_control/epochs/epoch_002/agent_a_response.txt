def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set((a, b) for a, b in observation.get("obstacles", []))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx if dx >= 0 else -dx if dy is None else max(dx if dx >= 0 else -dx, dy if dy >= 0 else -dy)

    # Deterministic target: push toward opponent territory centroid if present, else opponent position.
    if opp_ter:
        sx = sum(px for px, py in opp_ter); sy = sum(py for px, py in opp_ter)
        n = len(opp_ter)
        tx = sx // n; ty = sy // n
    else:
        tx, ty = observation["opponent_position"]

    # If unclaimed exists, bias toward the unclaimed cell closest to the target direction.
    if unclaimed:
        best_uc = None
        for ux, uy in unclaimed:
            # prefer closer to target, then closer to our current position
            dc = abs(ux - tx) + abs(uy - ty)
            ds = abs(ux - x) + abs(uy - y)
            cand = (dc, ds, uy, ux)
            if best_uc is None or cand < best_uc[0]:
                best_uc = (cand, (ux, uy))
        ux, uy = best_uc[1]
    else:
        ux, uy = tx, ty

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_move = (0, 0); best_score = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        dest = (nx, ny)
        base = 0
        if dest in opp_ter:
            base = 10
        elif dest in unclaimed:
            base = 4
        elif dest in self_ter:
            base = 1
        else:
            base = 0

        # Main push objective: shrink distance to selected unclaimed/centroid target
        dist1 = (abs(nx - ux) + abs(ny - uy))
        dist2 = (abs(nx - tx) + abs(ny - ty))
        score = base * 100 - dist1 * 3 - dist2

        # Mild stabilizer: avoid stepping "away" from the target when possible
        curd1 = (abs(x - ux) + abs(y - uy))
        if dist1 >= curd1:
            score -= 1

        if best_score is None or score > best_score:
            best_score = score; best_move = (dx, dy)

    return [best_move[0], best_move[1]]