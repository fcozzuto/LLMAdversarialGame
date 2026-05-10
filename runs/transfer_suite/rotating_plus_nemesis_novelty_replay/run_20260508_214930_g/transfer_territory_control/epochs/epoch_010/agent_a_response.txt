def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    un_set = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    options = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def min_dist_to_set(x, y, s):
        if not s:
            return 10**9
        best = 10**9
        for px, py in s:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    # frontier bias: prefer staying/advancing from cells adjacent to our territory
    def adj_to_self(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self_t:
                    return True
        return False

    # For each candidate neighbor cell, estimate "claim race" vs opponent to deny counterclaim.
    candidates = []
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        cell = (nx, ny)

        immediate = 0.0
        if cell in un_set:
            immediate += 80.0
        elif cell in opp_t:
            immediate += 40.0
        else:
            immediate += 4.0

        # denial: after moving, we want to be farther from opponent territory (harder to counterclaim),
        # but also move toward unclaimed.
        dist_opp = min_dist_to_set(nx, ny, opp_t)
        dist_un = min_dist_to_set(nx, ny, un_set)
        denial = 0.9 * dist_opp - 0.7 * dist_un

        # if choosing an unclaimed cell is likely to be stolen next, avoid it
        if cell in un_set:
            opp_closer = 0
            if opp_t:
                opp_closer = 1 if min_dist_to_set(ox, oy, {cell}) <= min_dist_to_set(sx, sy, {cell}) else 0
            # If opponent can reach as fast or faster, reduce priority
            denial -= 25.0 * opp_closer

        front = 12.0 if adj_to_self(nx, ny) or cell in self_t else 0.0
        center_bias = -0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        score = immediate + denial + front + center_bias
        # tie-break deterministically: prefer small dx,dy lexicographically
        candidates.append((score, abs(dx) + abs(dy), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]