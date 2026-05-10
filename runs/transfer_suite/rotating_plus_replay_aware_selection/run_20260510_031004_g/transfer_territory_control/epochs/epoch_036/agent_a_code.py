def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Targeting: go for nearest unclaimed; if none, go for nearest opponent-claimed cell to flip.
    targets = list(unclaimed) if unclaimed else []
    if not targets:
        targets = list(opp_terr)
    if targets:
        tx, ty = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]), -((t[0], t[1]) in unclaimed)))
    else:
        tx, ty = (sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        is_un = (nx, ny) in unclaimed
        is_self = (nx, ny) in self_terr
        is_opp = (nx, ny) in opp_terr

        if is_un:
            val += 280
        if is_self:
            val += 16
        if is_opp:
            val += 120  # flipping on entry is enabled

        # Voronoi-ish: prefer moves that decrease distance to target and increase distance from opponent
        d_t = max(1, max(abs(nx - tx), abs(ny - ty)))
        d_o = max(1, max(abs(nx - px), abs(ny - py)))
        val += 24 / d_t
        val += 8 * d_o / (w + h)

        # Avoid being too close to opponent unless it helps flipping
        adj_opp = max(abs(nx - px), abs(ny - py)) == 1
        if adj_opp and not is_opp:
            val -= 55

        # Small preference to expand rather than bounce: maintain direction to target
        cur_vec = (tx - sx, ty - sy)
        mv_vec = (nx - sx, ny - sy)
        if cur_vec != (0, 0) and mv_vec != (0, 0):
            dot = cur_vec[0] * mv_vec[0] + cur_vec[1] * mv_vec[1]
            val += 0.5 * dot

        # Deterministic tie-break: fixed dir order by strict comparison only
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]