def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        dx = 0 if ox == x else (1 if ox > x else -1)
        dy = 0 if oy == y else (1 if oy > y else -1)
        return [-dx, -dy]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b, c, d):
        return abs(a - b) + abs(c - d)

    def cell_value(tx, ty):
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        return lead * 1000 - d_me + (1 if d_me == 0 else 0)

    best = None
    bestv = None
    for tx, ty in resources:
        v = cell_value(tx, ty)
        if best is None or v > bestv or (v == bestv and (tx, ty) < best):
            best = (tx, ty)
            bestv = v
    tx, ty = best

    # Move choice: go toward target while avoiding obstacles and not walking into opponent.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            d_t = abs(tx - nx) + abs(ty - ny)
            d_o = abs(ox - nx) + abs(oy - ny)
            # Prefer steps that keep distance to opponent if we're not winning the local contest.
            d_me_now = abs(tx - nx) + abs(ty - ny)
            d_opp_now = abs(tx - ox) + abs(ty - oy)
            local_lead = d_opp_now - d_me_now
            score = d_t * 10 - d_o * (2 if local_lead <= 0 else 1)
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    if best_score is None:
        # All neighboring cells blocked: allow staying or first in-bounds move.
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]