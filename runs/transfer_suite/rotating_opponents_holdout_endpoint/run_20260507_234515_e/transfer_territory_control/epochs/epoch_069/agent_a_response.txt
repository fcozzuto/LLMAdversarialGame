def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base += 3
        elif (nx, ny) in opp_terr:
            base += 2
        elif (nx, ny) in self_terr:
            base += 0
        else:
            base += 1  # should be unclaimed, but keep safe

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        base += 0.05 * d_to_opp  # avoid immediate sweep contact

        # Prefer pushing toward regions the opponent is closer to (deny next entry)
        # by minimizing distance to the nearest unclaimed cell relative to opponent.
        best_rel = 10**9
        for ux, uy in unclaimed:
            if abs(ux - nx) + abs(uy - ny) > 5:
                continue
            rel = (abs(ux - nx) + abs(uy - ny)) - (abs(ux - ox) + abs(uy - oy))
            if rel < best_rel:
                best_rel = rel
        if best_rel < 10**9:
            base += 0.2 * (-best_rel)

        # Mild preference for staying near our current frontier (boundary cells tend to be best)
        adj_self = 0
        for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny+1), (nx-1, ny+1), (nx+1, ny-1)]:
            if (ax, ay) in self_terr:
                adj_self += 1
        base += 0.03 * adj_self

        candidates.append((base, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]