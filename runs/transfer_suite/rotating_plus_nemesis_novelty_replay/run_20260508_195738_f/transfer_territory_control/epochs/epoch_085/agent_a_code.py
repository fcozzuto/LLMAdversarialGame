def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(nx, ny, s):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in s:
                    c += 1
        return c

    def in_list(points, nx, ny):
        return (nx, ny) in points

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        a_self = adj_count(nx, ny, selft)
        a_opp = adj_count(nx, ny, opp)

        if in_list(unclaimed, nx, ny):
            score += 25.0 + 3.0 * a_self
        elif in_list(opp, nx, ny):
            score += 18.0 + 4.0 * a_self + 1.0 * a_opp
        elif in_list(selft, nx, ny):
            score += 2.0 + 1.0 * a_self
        else:
            score += 1.0 + 0.5 * a_self

        # Prefer pushing along the border: closeness to unclaimed or opponent near us
        if unclaimed:
            bestu = 10**9
            for ux, uy in unclaimed:
                d = abs(ux - nx) + abs(uy - ny)
                if d < bestu:
                    bestu = d
            score += max(0.0, 8.0 - 1.0 * bestu)
        if opp:
            beste = 10**9
            for ox, oy in opp:
                d = abs(ox - nx) + abs(oy - ny)
                if d < beste:
                    beste = d
            score += max(0.0, 6.0 - 0.8 * beste)

        # Slightly discourage staying still unless it's good for adjacency
        if dx == 0 and dy == 0:
            score -= 0.75
            score += 0.25 * a_self

        candidates.append((score, -a_self, -a_opp, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][3]), int(candidates[0][4])]