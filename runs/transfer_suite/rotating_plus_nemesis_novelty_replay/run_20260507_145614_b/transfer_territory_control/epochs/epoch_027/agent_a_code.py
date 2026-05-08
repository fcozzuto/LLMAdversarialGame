def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    unclaimed = {tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2}
    self_t = {tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2}
    opp_t = {tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2}
    obstacles = {tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2}

    cX, cY = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    bestv = -10**9

    def clamp01(t):
        if t < 0:
            return 0
        if t > 1:
            return 1
        return t

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        dcenter = abs(nx - cX) + abs(ny - cY)
        dopp = abs(nx - ox) + abs(ny - oy)

        if cell in opp_t:
            v = 900 - 3 * dcenter - dToB(1)
        elif cell in unclaimed:
            # Prefer center, and prefer stealing near opponent.
            v = 300 - 2 * dcenter - 0.6 * dfast(dopp) + 0.2 * (3 if opp_t else 0)
        elif cell in self_t:
            v = 40 - 0.7 * dcenter - 0.2 * dfast(dopp)
        else:
            v = 15 - 1.2 * dcenter - 0.1 * dfast(dopp)

        # If opponent controls a cell, strongly prefer unclaimed neighbors to frontload flips.
        if opp_t and cell not in opp_t:
            for ax, ay in ((nx + ddx, ny + ddy) for ddx in (-1, 0, 1) for ddy in (-1, 0, 1) if not (ddx == 0 and ddy == 0)):
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in opp_t:
                    if cell in unclaimed:
                        v += 250
                    elif cell in self_t:
                        v += 35
                    else:
                        v += 10

        # Mild obstacle/terrain neutrality already handled; tie-break deterministically.
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    # If all moves were blocked by obstacles (rare), stay.
    return [int(best[0]), int(best[1])]

def dfast(d):
    return d

def dToB(_):
    return 0