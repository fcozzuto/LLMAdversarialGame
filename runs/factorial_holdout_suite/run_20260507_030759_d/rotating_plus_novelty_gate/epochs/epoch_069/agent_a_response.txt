def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    resset = set((p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2)

    if (sx, sy) in resset:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal or not resset:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opppos = (ox, oy)

    # Contest policy: pick a resource where we are closer (or at least not much farther).
    best_target = None
    best_key = None
    for r in resset:
        dm = dist(mypos, r)
        do = dist(opppos, r)
        # Prefer winning contests; then nearer resources; then deterministic tie-break.
        key = (dm - do, dm, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = r

    tx, ty = best_target

    # 2-step greedy refinement: choose move that minimizes distance to target, with obstacle-safe bias.
    best_move = None
    best_val = None
    for mdx, mdy in legal:
        nx, ny = sx + mdx, sy + mdy
        if (nx, ny) in resset:
            return [mdx, mdy]
        d1 = abs(nx - tx) + abs(ny - ty)

        # Evaluate best continuation from next position (still deterministic, small depth).
        cont = 10**9
        for sdx in (-1, 0, 1):
            for sdy in (-1, 0, 1):
                nnx, nny = nx + sdx, ny + sdy
                if 0 <= nnx < w and 0 <= nny < h and (nnx, nny) not in obstacles:
                    if (nnx, nny) in resset:
                        cont = 0
                        break
                    cont = min(cont, abs(nnx - tx) + abs(nny - ty))
            if cont == 0:
                break

        # Also discourage moves that move closer to opponent in Manhattan sense (simple deny).
        deny = abs(nx - ox) + abs(ny - oy)
        val = (d1, cont, -deny, mdx, mdy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]