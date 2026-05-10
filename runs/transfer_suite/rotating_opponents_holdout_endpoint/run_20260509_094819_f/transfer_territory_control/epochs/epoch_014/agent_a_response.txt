def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_dist_to_set(x, y, s):
        if not s:
            return abs(x - ox) + abs(y - oy)
        md = 10**9
        for tx, ty in s:
            d = abs(x - tx) + abs(y - ty)
            if d < md:
                md = d
        return md

    def score_cell(x, y):
        cell = (x, y)
        dO = abs(x - ox) + abs(y - oy)
        dOppTerr = min_dist_to_set(x, y, opp_terr)
        if cell in obstacles:
            return -10**9
        # Immediate value: stealing/control swing first
        if cell in opp_terr:
            steal = 200 - dO
        elif cell in unclaimed:
            # Prefer capturing near opponent
            steal = 60 - 2 * dOppTerr
        elif cell in self_terr:
            # Prefer continuing from border towards opponent, not deep inside
            border_bias = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and ((nx, ny) in opp_terr or (nx, ny) in unclaimed):
                    border_bias = 8
                    break
            steal = 5 + border_bias - dOppTerr
        else:
            # Any other reachable cell (shouldn't often happen)
            steal = 10 - dOppTerr
        # Mild penalty for moving away from opponent if we are behind
        selfc = int(observation.get("self_territory_count", 0) or 0)
        oppc = int(observation.get("opponent_territory_count", 0) or 0)
        behind = 1 if selfc <= oppc else 0
        pos_pen = (2 * dOppTerr + dO) if behind else dOppTerr
        return steal - pos_pen

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = score_cell(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = v
            best_move = [dx, dy]

    return best_move