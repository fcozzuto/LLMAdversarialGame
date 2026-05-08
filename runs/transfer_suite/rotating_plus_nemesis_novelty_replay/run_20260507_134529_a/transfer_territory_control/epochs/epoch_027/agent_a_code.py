def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Heuristic: claim/flip while pushing toward center and away from opponent pressure.
        n_is_self = (nx, ny) in self_terr
        n_is_opp = (nx, ny) in opp_terr
        n_is_un = (nx, ny) in unclaimed
        if not (n_is_self or n_is_opp or n_is_un):
            # still okay if it's some other claimed cell; treat neutrally
            n_is_unk = True
        else:
            n_is_unk = False

        center_before = abs(sx - cx) + abs(sy - cy)
        center_after = abs(nx - cx) + abs(ny - cy)
        opp_before = abs(sx - ox) + abs(sy - oy)
        opp_after = abs(nx - ox) + abs(ny - oy)

        # Value components
        v = 0.0
        v += (center_before - center_after) * 2.0          # move toward center
        v += (opp_after - opp_before) * 0.35             # avoid opponent if possible
        if n_is_un:
            v += 1.2                                       # expansion into unclaimed
        if n_is_opp:
            v += 2.6                                       # flipping on entry is strong
        if n_is_self:
            v -= 0.05                                      # slight penalty for not expanding

        # Tie-break deterministically: prefer larger v, then closer to center, then farther from opponent, then lexicographic move.
        if best is None or v > bestv + 1e-12:
            bestv = v
            best = (dx, dy, center_after, -opp_after)
        elif abs(v - bestv) <= 1e-12:
            cand = (dx, dy, abs(nx - cx) + abs(ny - cy), -abs(nx - ox) - abs(ny - oy))
            # smaller center_after preferred; then smaller cand tuple ordering by dx,dy deterministically
            if cand[2] < best[2] - 1e-12 or (abs(cand[2] - best[2]) <= 1e-12 and cand[3] < best[3] - 1e-12):
                best = (dx, dy, cand[2], cand[3])

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]