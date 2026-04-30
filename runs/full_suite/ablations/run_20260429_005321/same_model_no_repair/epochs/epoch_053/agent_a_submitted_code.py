def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    blocked = set((x, y) for x, y in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_risk(x, y):
        # small penalty for being adjacent to obstacles to avoid trapping/denial
        r = 0
        for (bx, by) in blocked:
            if abs(bx - x) <= 1 and abs(by - y) <= 1:
                if (bx, by) != (x, y):
                    r += 1
        return r

    # Prefer states that keep/extend distance advantage to a promising resource.
    best_dx, best_dy = 0, 0
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue

            # Evaluate best target from this next cell.
            local = -10**18
            myd = 0
            for tx, ty in resources:
                if (tx, ty) in blocked:
                    continue
                ds = man(nx, ny, tx, ty)
                do = man(ox, oy, tx, ty)
                # If we can arrive sooner, it should dominate. Also include "reach quality".
                val = (do - ds) * 10 - ds - cell_risk(nx, ny) * 2
                if val > local:
                    local = val
                    myd = ds

            # If targets are all bad, fall back to moving toward the closest resource
            if local == -10**18:
                local = -cell_risk(nx, ny) - min(m an(nx, ny, tx, ty) for tx, ty in resources)

            # Mild tie-break: avoid drifting away from resources when values are equal.
            if local > best_val or (local == best_val and man(nx, ny, resources[0][0], resources[0][1]) < man(sx, sy, resources[0][0], resources[0][1])):
                best_val = local
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]